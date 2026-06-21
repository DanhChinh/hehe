const footer_text = `
  <footer class="footer-custom pt-5 pb-4">
    <div class="container">
      <div class="row">

        <div class="col-md-4 mb-4">
          <h5 class="fw-bold text-white mb-3">MyWebsite</h5>
          <p class="text-muted fs-6">
            Nền tảng chia sẻ kiến thức công nghệ, lập trình và AI.
          </p>
        </div>

        <div class="col-md-2 mb-4">
          <h6 class="fw-bold text-white mb-3">Liên kết</h6>
          <ul class="list-unstyled d-flex flex-column gap-2">
            <li><a href="#" class="footer-link text-decoration-none">Trang chủ</a></li>
            <li><a href="#" class="footer-link text-decoration-none">Giới thiệu</a></li>
            <li><a href="#" class="footer-link text-decoration-none">Dịch vụ</a></li>
            <li><a href="#" class="footer-link text-decoration-none">Liên hệ</a></li>
          </ul>
        </div>

        <div class="col-md-3 mb-4">
          <h6 class="fw-bold text-white mb-3">Hỗ trợ</h6>
          <ul class="list-unstyled d-flex flex-column gap-2">
            <li><a href="#" class="footer-link text-decoration-none">FAQ</a></li>
            <li><a href="#" class="footer-link text-decoration-none">Chính sách bảo mật</a></li>
            <li><a href="#" class="footer-link text-decoration-none">Điều khoản dịch vụ</a></li>
          </ul>
        </div>

        <div class="col-md-3 mb-4">
          <h6 class="fw-bold text-white mb-3">Liên hệ</h6>
          <p class="text-muted mb-2">📍 Việt Nam</p>
          <p class="text-muted mb-2">📧 contact@email.com</p>
          <p class="text-muted">📞 0123 456 789</p>

          <div class="d-flex gap-3 mt-3">
            <a href="#" class="footer-icon"><i class="bi bi-facebook"></i></a>
            <a href="#" class="footer-icon"><i class="bi bi-github"></i></a>
            <a href="#" class="footer-icon"><i class="bi bi-youtube"></i></a>
          </div>
        </div>

      </div>

      <hr class="footer-divider my-4">

      <div class="text-center text-muted fs-7">
        © 2026 MyWebsite. All rights reserved.
      </div>
    </div>
  </footer>
`;

document.getElementsByTagName('footer')[0].innerHTML = footer_text;