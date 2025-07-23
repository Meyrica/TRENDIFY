function login(event) {
  event.preventDefault();
  const email = document.getElementById("email").value.toLowerCase();
  const password = document.getElementById("password").value;

  fetch("/api/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ email, password })
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      alert("Login successful!");
      if (data.role === 'admin') {
        window.location.href = "/dashboard";
      } else {
        window.location.href = "/";
      }
    } else {
      alert(data.message || "Login Failed.");
    }
  })
  .catch(error => {
    console.error("Terjadi kesalahan:", error);
    alert("Gagal terhubung ke server.");
  });
}
