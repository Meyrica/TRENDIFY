fetch('/api/products')
  .then(response => response.json())
  .then(data => {
    const container = document.getElementById('product-cards');
    if (data.length === 0) {
      container.innerHTML = '<p style="text-align:center; color:#888;">Belum ada produk tersedia.</p>';
      return;
    }

    data.forEach(product => {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <img src="/static/uploads/${product.image_path}" alt="${product.title}">
        <h3>${product.title}</h3>
        <p>Rp ${Number(product.price).toLocaleString('id-ID')}</p>
        <p style="font-size: 12px; color: #999;">${product.artist}</p>
        <button onclick="window.location.href='/product/${product.id}'">View</button>
      `;
      container.appendChild(card);
    });
  })
  .catch(err => {
    document.getElementById('product-cards').innerHTML = '<p style="color:red;">Gagal memuat produk.</p>';
    console.error(err);
  });
