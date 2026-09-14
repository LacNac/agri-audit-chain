import { useState } from "react";
import "./App.css";
import agritrace from "./assets/Agritrace.svg";
import name from "./assets/name.svg";
import fruit from "./assets/fruit.svg";

function App() {
  return (
    <>
      <nav className="navbar">
        <div className="logo-group">
          <img src={name} alt="Logo AgriTrace" className="logo" />
          <img src={agritrace} alt="..." className="logo2" />
        </div>

        <ul className="nav-menu">
          <li>
            <a>Trang chủ</a>
          </li>
          <li>
            <a>Sản phẩm</a>
          </li>
          <li>
            <a>Về chúng tôi </a>
          </li>
        </ul>

        <div className="nav-login">
          <a>Đăng nhập</a>
          <button>Tạo tài khoản miễn phí →</button>
        </div>
      </nav>
      <div className="ticks"></div>
      <section id="spacer"></section>
      <main className="introduce">
        <section className="hero">
          <div className="trace">
            <p className="up">NỀN TẢNG HỒ SƠ SỐ NÔNG SẢN</p>
            <h1 className="hero-title">
              MỖI NÔNG SẢN. <br />
              <span className="purple-text">MỘT DANH TÍNH SỐ.</span>
            </h1>
            <p className="down">
              Số hóa quy trình canh tác, chuỗi cung ứng và kiểm định chất lượng
              thành hồ sơ số minh bạch, giúp nông sản Việt tự tin vươn xa.
            </p>
            <div className="check">
              <button>Quét mã truy xuất</button>
              <button>Tìm kiếm mã nông sản</button>
            </div>
            <p className="trust-text">
              Chuỗi khối an toàn • Mã QR định danh • Dữ liệu bất biến
            </p>
          </div>
          <div className="hero-image">
            <img src={fruit} alt="" className="fruit"></img>
          </div>
        </section>
        <div className="floating-actions">
          <button className="fab-btn qr-btn">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <rect x="3" y="3" width="7" height="7" rx="1.5" />
              <rect x="14" y="3" width="7" height="7" rx="1.5" />
              <rect x="3" y="14" width="7" height="7" rx="1.5" />
              <rect x="14" y="14" width="7" height="7" rx="1.5" />
            </svg>
          </button>

          <button className="fab-btn bot-btn">
            <img
              src="https://api.dicebear.com/7.x/bottts/svg?seed=AgriBotPurple"
              alt="Bot Support"
            />
          </button>

          <button className="fab-btn call-btn">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24c1.12.37 2.33.57 3.58.57a1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.25.2 2.46.57 3.58a1 1 0 01-.24 1.01l-2.21 2.2z" />
            </svg>
          </button>
        </div>
      </main>
    </>
  );
}

export default App;
