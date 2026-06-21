const header_text = `
<nav class="navbar navbar-expand-lg navbar-dark navbar-custom sticky-top shadow-sm">
  <div class="container">
    
    <a class="navbar-brand fw-bold text-white fs-5" href="#">
      MyWebsite
    </a>

    <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#mainNavbar">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="mainNavbar">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item">
          <a class="nav-link active" href="#">Trang chủ</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="#">Giới thiệu</a>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
            Dịch vụ
          </a>
          <ul class="dropdown-menu dropdown-menu-dark shadow">
            <li><a class="dropdown-item" href="#">Web Development</a></li>
            <li><a class="dropdown-item" href="#">AI & ML</a></li>
            <li><a class="dropdown-item" href="#">Mobile App</a></li>
          </ul>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="#">Liên hệ</a>
        </li>
      </ul>

      <form class="position-relative me-3 d-none d-lg-block" style="width: 280px;">
        <input 
            id="DOM_accessToken"
            type="search"
            class="form-control form-control-sm navbar-search"
            placeholder="Tìm kiếm..."
        >
        <button 
            type="submit"
            class="btn position-absolute top-50 end-0 translate-middle-y me-2 p-0 border-0 bg-transparent text-muted"
        >
            <i class="bi bi-search"></i>
        </button>
      </form>

      <div class="d-flex gap-2">
        <a id="DOM_isConnectGame" href="#" class="btn btn-sm btn-nav-secondary">Đăng nhập</a>
        <a id="DOM_connectPyserver" href="#" class="btn btn-sm btn-nav-primary">Đăng ký</a>
      </div>
    </div>
  </div>
</nav>
`;

document.getElementsByTagName('header')[0].innerHTML = header_text;