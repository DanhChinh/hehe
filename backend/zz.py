import numpy as np
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
import time

# --- 1. LỚP QUẢN LÝ AGENT (Hệ thống dữ liệu Z-Score & Mapping) ---
class AgentManager:
    def __init__(self, n_agents=100, window_size=30):
        self.n_agents = n_agents
        self.window_size = window_size
        self.history = np.empty((n_agents, 0))
        self.current_preds = None

    def get_ensemble_pred(self):
        # Giả lập dự đoán của đám đông Agent
        self.current_preds = np.random.randint(0, 2, self.n_agents)
        n1 = np.sum(self.current_preds)
        return 1 if n1 >= (self.n_agents / 2) else 0

    def _calculate_z(self, data_series):
        if len(data_series) < self.window_size: return 0.0
        recent = data_series[-self.window_size:]
        mu = np.mean(recent)
        std = np.std(recent) + 1e-9
        return (data_series[-1] - mu) / std

    def get_z_score(self):
        if self.history.shape[1] < self.window_size: return 0.0
        all_cum = np.cumsum(self.history, axis=1)
        avg_wave = np.mean(all_cum, axis=0)
        return self._calculate_z(avg_wave)

    def get_asymmetric_deltas(self):
        """
        TÍNH TOÁN TRƯỚC KHI CÓ KẾT QUẢ:
        Xác định Z-score sẽ thay đổi bao nhiêu trong cả 2 kịch bản Thắng/Thua.
        """
        if self.history.shape[1] < self.window_size:
            return 0.0, 0.0
        
        all_cum = np.cumsum(self.history, axis=1)
        avg_wave = np.mean(all_cum, axis=0)
        z_now = self._calculate_z(avg_wave)
        
        # Dự đoán hiện tại của Ensemble
        pred = 1 if np.sum(self.current_preds) >= (self.n_agents/2) else 0
        
        # Kịch bản 1: THẮNG (Kết quả thực tế trùng với dự đoán)
        matches_win = np.where(self.current_preds == pred, 1, -1)
        new_point_win = avg_wave[-1] + np.mean(matches_win)
        z_if_win = self._calculate_z(np.append(avg_wave, new_point_win))
        delta_up = max(0, z_if_win - z_now)
        
        # Kịch bản 2: THUA (Kết quả thực tế ngược với dự đoán)
        matches_loss = np.where(self.current_preds != pred, 1, -1)
        new_point_loss = avg_wave[-1] + np.mean(matches_loss)
        z_if_loss = self._calculate_z(np.append(avg_wave, new_point_loss))
        delta_down = max(0, z_now - z_if_loss)
        
        return delta_up, delta_down

    def update_history(self, actual):
        matches = np.where(self.current_preds == actual, 1, -1)
        self.history = np.hstack([self.history, matches.reshape(-1, 1)])

# --- 2. LỚP QUẢN LÝ TRADE (Logic cược & Lưu trữ chu kỳ) ---
class TradingSystem:
    def __init__(self, multiplier=5000):
        self.balance = 1000.0
        self.multiplier = multiplier
        self.in_streak = False
        self.cycle_logs = []
        
        # Thống kê On-streak hiện tại
        self.streak_wins = 0
        self.streak_losses = 0
        self.streak_start_balance = 0.0
        self.streak_start_sid = 0
        
        # Kỷ lục liên tiếp toàn thời gian
        self.last_status = None
        self.consecutive_count = 0
        self.max_win_streak = 0
        self.max_loss_streak = 0

    def record_result(self, is_win, delta_up, delta_down):
        # Ánh xạ lượng tiền cược theo đúng delta tương ứng của Z-score
        actual_delta = delta_up if is_win else delta_down
        bet_amount = actual_delta * self.multiplier
        
        if is_win:
            self.balance += bet_amount
            self.streak_wins += 1
            status = "WIN"
        else:
            self.balance -= bet_amount
            self.streak_losses += 1
            status = "LOSS"
            
        # Cập nhật kỷ lục chuỗi
        if status == self.last_status:
            self.consecutive_count += 1
        else:
            self.last_status = status
            self.consecutive_count = 1
        
        if is_win: self.max_win_streak = max(self.max_win_streak, self.consecutive_count)
        else: self.max_loss_streak = max(self.max_loss_streak, self.consecutive_count)
        
        return bet_amount

# --- 3. THỰC THI HỆ THỐNG ---
if __name__ == "__main__":
    console = Console()
    agents = AgentManager(window_size=30)
    bot = TradingSystem(multiplier=6000)

    # Setup đồ thị Matplotlib
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    eq_line, = ax1.plot([], [], color='#2ecc71', label='Equity (Shadowing Z)')
    z_line, = ax2.plot([], [], color='#3498db', label='Z-Score')
    ax2.axhline(-2.0, color='#e74c3c', ls='--')
    ax2.axhline(2.0, color='#2ecc71', ls='--')
    ax1.set_ylabel("Balance"); ax2.set_ylabel("Z-Score")
    
    x_data, eq_data, z_data = [], [], []
    sid = 0

    with Live(console=console, refresh_per_second=15) as live:
        while len(bot.cycle_logs) < 15: # Chạy đến khi hoàn thành 5 chu kỳ
            sid += 1
            z_now = agents.get_z_score()
            pred = agents.get_ensemble_pred()
            
            # 1. TÍNH TOÁN BET TRƯỚC KHI CÓ KẾT QUẢ
            d_up, d_down = agents.get_asymmetric_deltas()
            
            # Logic quản lý Chu kỳ (On-streak)
            if not bot.in_streak and z_now <= -2.0:
                bot.in_streak = True
                bot.streak_wins = 0; bot.streak_losses = 0
                bot.streak_start_balance = bot.balance
                bot.streak_start_sid = sid
                console.print(f"[bold yellow]T{sid} >>> BẮT ĐẦU CHU KỲ HỒI PHỤC (Z={z_now:.2f})[/]")

            # 2. XÁC ĐỊNH KẾT QUẢ THỰC TẾ
            actual = np.random.randint(0, 2)
            is_win = (pred == actual)
            
            # 3. GHI NHẬN VÀ CẬP NHẬT
            current_bet = 0
            if bot.in_streak:
                current_bet = bot.record_result(is_win, d_up, d_down)
            
            agents.update_history(actual)
            
            # Kết thúc chu kỳ khi Z chạm ngưỡng trên
            if bot.in_streak and z_now >= 2.0:
                bot.in_streak = False
                profit = bot.balance - bot.streak_start_balance
                duration = sid - bot.streak_start_sid
                log = {"id": len(bot.cycle_logs)+1, "w": bot.streak_wins, "l": bot.streak_losses, "p": profit, "d": duration}
                bot.cycle_logs.append(log)
                
                # In bảng tổng kết nhanh chu kỳ
                c_table = Table(box=None)
                c_table.add_column("Cycle", style="magenta")
                c_table.add_column("W/L", justify="center")
                c_table.add_column("Profit", style="bold green" if profit > 0 else "bold red")
                c_table.add_row(f"#{log['id']}", f"{log['w']}W-{log['l']}L", f"{profit:+.2f}")
                console.print(Panel(c_table, title="Cycle Complete", border_style="magenta"))

            # --- VISUALIZATION ---
            x_data.append(sid); eq_data.append(bot.balance); z_data.append(z_now)
            eq_line.set_data(x_data, eq_data); z_line.set_data(x_data, z_data)
            for ax in [ax1, ax2]: ax.relim(); ax.autoscale_view()
            plt.pause(0.001)

            # Rich Table UI
            table = Table(title="Z-SCORE SHADOW MAPPING ENGINE v2.0", expand=True)
            table.add_column("SID", justify="center")
            table.add_column("Z-Score", style="cyan")
            table.add_column("On-Streak W/L", justify="center", style="bold yellow")
            table.add_column("Est. Risk/Reward", justify="center")
            table.add_column("Balance", style="bold white", justify="right")

            rr_str = f"[green]+{d_up*bot.multiplier:.1f}[/] / [red]-{d_down*bot.multiplier:.1f}[/]" if bot.in_streak else "-"
            s_color = "green" if bot.last_status == "WIN" else "red"
            streak_str = f"[{s_color}]{bot.last_status} x{bot.consecutive_count}[/]" if bot.last_status else "-"

            table.add_row(
                str(sid), 
                f"{z_now:.3f}", 
                f"{bot.streak_wins}W - {bot.streak_losses}L" if bot.in_streak else "[dim]Idle[/]",
                rr_str,
                f"{bot.balance:.2f}"
            )
            
            footer = f"Cycles: {len(bot.cycle_logs)}/5 | Max Streak: {bot.max_win_streak}W / {bot.max_loss_streak}L | Bet: {current_bet:.2f}"
            live.update(Panel(table, subtitle=footer, border_style="blue"))

    # KẾT THÚC TOÀN BỘ
    final_table = Table(title="📊 FINAL PERFORMANCE REPORT", title_style="bold yellow", show_lines=True)
    final_table.add_column("Cycle #"); final_table.add_column("Win Rate"); final_table.add_column("Net Profit"); final_table.add_column("Duration")
    
    for l in bot.cycle_logs:
        wr = (l['w']/(l['w']+l['l'])*100) if (l['w']+l['l']) > 0 else 0
        final_table.add_row(str(l['id']), f"{wr:.1f}%", f"{l['p']:+.2f}", f"{l['d']} steps")
    
    console.print("\n", final_table)
    plt.ioff(); plt.show()