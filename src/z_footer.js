const footer_text = `
  <footer class="bg-dark text-light pt-5 pb-4">
    <div class="container">
      <div class="row">

        <!-- Logo & Description -->
        <div class="col-md-4 mb-4">
          <h5 class="fw-bold">MyWebsite</h5>
          <p class="">
            Nền tảng chia sẻ kiến thức công nghệ, lập trình và AI.
          </p>
        </div>

        <!-- Quick Links -->
        <div class="col-md-2 mb-4">
          <h6 class="fw-bold">Liên kết</h6>
          <ul class="list-unstyled">
            <li><a href="#" class=" text-decoration-none">Trang chủ</a></li>
            <li><a href="#" class=" text-decoration-none">Giới thiệu</a></li>
            <li><a href="#" class=" text-decoration-none">Dịch vụ</a></li>
            <li><a href="#" class=" text-decoration-none">Liên hệ</a></li>
          </ul>
        </div>

        <!-- Support -->
        <div class="col-md-3 mb-4">
          <h6 class="fw-bold">Hỗ trợ</h6>
          <ul class="list-unstyled">
            <li><a href="#" class=" text-decoration-none">FAQ</a></li>
            <li><a href="#" class=" text-decoration-none">Chính sách</a></li>
            <li><a href="#" class=" text-decoration-none">Điều khoản</a></li>
          </ul>
        </div>

        <!-- Contact -->
        <div class="col-md-3 mb-4">
          <h6 class="fw-bold">Liên hệ</h6>
          <p class=" mb-1">📍 Việt Nam</p>
          <p class=" mb-1">📧 contact@email.com</p>
          <p class="">📞 0123 456 789</p>

          <!-- Social icons -->
          <div class="d-flex gap-3 mt-2">
            <a href="#" class="text-light fs-5"><i class="bi bi-facebook"></i></a>
            <a href="#" class="text-light fs-5"><i class="bi bi-github"></i></a>
            <a href="#" class="text-light fs-5"><i class="bi bi-youtube"></i></a>
          </div>
        </div>

      </div>

      <hr class="border-secondary">

      <!-- Copyright -->
      <div class="text-center ">
        © 2025 MyWebsite. All rights reserved.
      </div>
    </div>
  </footer>
`
document.getElementsByTagName('footer')[0].innerHTML = footer_text;
