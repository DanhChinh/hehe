function hideScrollbars() {
    document.documentElement.style.overflow = 'auto';
    document.body.style.overflow = 'auto';

    // Chrome, Safari
    document.documentElement.style.scrollbarWidth = 'none';
    document.body.style.scrollbarWidth = 'none';

    // IE, Edge
    document.documentElement.style.msOverflowStyle = 'none';
    document.body.style.msOverflowStyle = 'none';
}

// Gọi khi trang load
document.addEventListener("DOMContentLoaded", hideScrollbars);

// Gọi khi resize
window.addEventListener("resize", hideScrollbars);

// Gọi khi nội dung DOM thay đổi
const observer = new MutationObserver(hideScrollbars);
observer.observe(document.body, { childList: true, subtree: true });