// static/js/all_products.js
document.addEventListener("DOMContentLoaded", function () {
  fetch("/api/products")
    .then((response) => response.json())
    .then((products) => {
      const container = document.getElementById("productGrid");

      if (products.length === 0) {
        container.innerHTML = `<div class="no-product">Belum ada produk.</div>`;
      } else {
        products.forEach((product) => {
          const card = document.createElement("div");
          card.className = "product-card";
          card.innerHTML = `
            <a href="/product/${product.id}" style="text-decoration:none;color:inherit">
              <img src="/static/uploads/${product.image_path}" alt="${product.title}" />
              <h2>${product.title}</h2>
              <p>Rp ${Number(product.price).toLocaleString('id-ID')}</p>
            </a>
          `;
          container.appendChild(card);
        });
      }
    })
    .catch((error) => {
      console.error("Gagal ambil data:", error);
    });
});

