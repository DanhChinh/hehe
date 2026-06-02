import numpy as np
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

# --- 1. LỚP QUẢN LÝ AGENT (DATA ENGINE) ---
class AgentManager:
    def __init__(self, n_agents=100, window_size=25):
        """
        Khởi tạo hệ thống Agent với kiến thức về xử lý dữ liệu chuỗi thời gian.
        """
        self.n_agents = n_agents
        self.window_size = window_size
        self.history = np.empty((n_agents, 0))
        self.current_preds = None

    def get_ensemble_pred(self):
        """Trả về dự đoán số đông."""
        self.current_preds = np.random.randint(0, 2, self.n_agents)
        n1 = np.sum(self.current_preds)
        n0 = self.n_agents - n1
        pred = 1 if n1 >= n0 else 0
        return pred

    def _calculate_hypothetical_z(self, avg_wave, new_point):
        """Hàm phụ trợ tính Z-score cho một điểm giả định trong tương lai."""
        window = np.append(avg_wave[-(self.window_size-1):], new_point)
        mu = np.mean(window)
        std = np.std(window) + 1e-9
        return (new_point - mu) / std

    def get_symmetric_delta_z(self):
        """
        TÍNH TOÁN QUYẾT ĐỊNH: Lấy trung bình Delta Z của 2 kịch bản (Thắng/Thua).
        Giúp Balance tịnh tiến đồng bộ với đồ thị Z-score.
        """
        if self.history.shape[1] < self.window_size:
            return 0.0

        # Trạng thái hiện tại
        z_now = self.get_z_score()
        all_cum = np.cumsum(self.history, axis=1)
        avg_wave = np.mean(all_cum, axis=0)
        
        # Kịch bản 1: Kết quả ra 1
        shift_1 = (np.sum(self.current_preds == 1) - np.sum(self.current_preds == 0)) / self.n_agents
        z_if_1 = self._calculate_hypothetical_z(avg_wave, avg_wave[-1] + shift_1)
        delta_1 = abs(z_if_1 - z_now)

        # Kịch bản 0: Kết quả ra 0
        shift_0 = (np.sum(self.current_preds == 0) - np.sum(self.current_preds == 1)) / self.n_agents
        z_if_0 = self._calculate_hypothetical_z(avg_wave, avg_wave[-1] + shift_0)
        delta_0 = abs(z_if_0 - z_now)

        # Trả về trung bình cộng để triệt tiêu sự bất đối xứng toán học
        return (delta_1 + delta_0) / 2

    def update_history(self, actual_result):
        """Cập nhật lịch sử khớp với kết quả sàn thực tế."""
        if self.current_preds is None: return
        matches = np.where(self.current_preds == actual_result, 1, -1)
        self.history = np.hstack([self.history, matches.reshape(-1, 1)])

    def get_z_score(self):
        """Tính Z-score hiện tại của Ensemble Wave."""
        if self.history.shape[1] < self.window_size:
            return 0
        all_cum = np.cumsum(self.history, axis=1)
        avg_wave = np.mean(all_cum, axis=0)
        recent = avg_wave[-self.window_size:]
        mean, std = np.mean(recent), np.std(recent) + 1e-9
        return (avg_wave[-1] - mean) / std

# --- 2. LỚP QUẢN LÝ TRADE (ĐỒNG BỘ TỊNH TIẾN) ---
class TradingSystem:
    def __init__(self, initial_balance=1000, multiplier=2000):
        self.balance = initial_balance
        self.multiplier = multiplier
        self.in_streak = False
        self.streak_count = 0
        self.my_pred = None
        self.current_z = 0
        self.current_bet = 0

    def decide(self, z_score, ensemble_pred, symmetric_delta):
        self.current_z = z_score

        # Điểm kết thúc chu kỳ (Z hồi phục về biên trên)
        if self.in_streak and z_score >= 2.0:
            self.in_streak = False
            self.streak_count += 1
            self.my_pred = None
            self.current_bet = 0
            return f"FINISHED CYCLE {self.streak_count}"

        # Điểm bắt đầu chu kỳ (Z chạm đáy)
        if not self.in_streak and z_score <= -2.0:
            self.in_streak = True

        # Trong chu kỳ: Cược dựa trên biến thiên Z đồng bộ
        if self.in_streak:
            self.my_pred = ensemble_pred
            self.current_bet = symmetric_delta * self.multiplier
        else:
            self.my_pred = None
            self.current_bet = 0
            
        return None

    def record_result(self, actual_result):
        if self.my_pred is None: return
        is_win = (self.my_pred == actual_result)
        # Bỏ qua phí sàn theo yêu cầu để theo dõi tính tịnh tiến thuần túy
        profit = self.current_bet if is_win else -self.current_bet
        self.balance += profit

# --- 3. KHỞI CHẠY (Sử dụng Rich và Matplotlib cho visualization) ---
if __name__ == "__main__":
    console = Console()
    agents = AgentManager(window_size=30)
    bot = TradingSystem(multiplier=3000) # Hệ số nhân cao để thấy rõ sự tương quan

    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    equity_line, = ax1.plot([], [], color='forestgreen', label='Equity (Balance)')
    z_line, = ax2.plot([], [], color='dodgerblue', alpha=0.7, label='Z-Score')
    ax2.axhline(-2.0, color='red', linestyle='--')
    ax2.axhline(2.0, color='green', linestyle='--')
    ax1.legend(); ax2.legend()

    equity_data, z_data, x_data = [], [], []
    sid = 0

    with Live(console=console, refresh_per_second=10) as live:
        while bot.streak_count < 50:
            sid += 1
            
            # Bước 1: Lấy thông tin phiên
            z_val = agents.get_z_score()
            pred = agents.get_ensemble_pred()
            
            # Bước 2: Tính Delta Z đối xứng trước khi cược
            sym_delta = agents.get_symmetric_delta_z()
            
            # Bước 3: Bot đặt cược
            msg = bot.decide(z_val, pred, sym_delta)
            if msg: console.print(f"[bold cyan]ℹ️ {msg}[/]")

            # Bước 4: Kết quả thực tế
            actual = np.random.randint(0, 2)
            agents.update_history(actual)
            bot.record_result(actual)
            
            # Cập nhật đồ thị
            x_data.append(sid)
            equity_data.append(bot.balance)
            z_data.append(z_val)
            
            ax1.set_xlim(0, sid + 10)
            ax1.set_ylim(min(equity_data)-50, max(equity_data)+50)
            equity_line.set_data(x_data, equity_data)
            ax2.set_xlim(0, sid + 10)
            ax2.set_ylim(-5, 5)
            z_line.set_data(x_data, z_data)
            plt.pause(0.01)

            # Hiển thị bảng Live
            table = Table(title="SYNCED Z-SCORE TRADING SYSTEM")
            table.add_column("SID")
            table.add_column("Z-Score", style="cyan")
            table.add_column("Sym Delta Z", style="magenta")
            table.add_column("Bet", style="yellow")
            table.add_column("Balance", style="green bold")

            st = "[bold yellow]ON-STREAK[/]" if bot.in_streak else "[dim]WAITING[/]"
            table.add_row(str(sid), f"{z_val:.3f}", f"{sym_delta:.4f}", f"{bot.current_bet:.2f}", f"{bot.balance:.2f}")
            live.update(Panel.fit(table, subtitle=f"Status: {st} | Cycles: {bot.streak_count}/5"))

    plt.ioff()
    plt.show()