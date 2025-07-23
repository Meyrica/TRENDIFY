// // static/js/payment.js
// document.addEventListener("DOMContentLoaded", function () {
//   const payButton = document.getElementById("pay-button");

//   if (payButton) {
//     payButton.addEventListener("click", function () {
//       const productId = this.dataset.productId;

//       fetch("/create_transaction", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json"
//         },
//         body: JSON.stringify({ product_id: productId })
//       })
//       .then(response => response.json())
//       .then(data => {
//         if (data.token) {
//           snap.pay(data.token);
//         } else {
//           alert("Gagal memproses transaksi.");
//         }
//       })
//       .catch(error => {
//         console.error("Error:", error);
//         alert("Terjadi kesalahan.");
//       });
//     });
//   }
// });



document.addEventListener("DOMContentLoaded", function () {
  const payButton = document.getElementById("pay-button");

  if (payButton) {
    payButton.addEventListener("click", function () {
      if (!isLoggedIn) {
        alert("You must be logged in before purchasing.");
        return;
      }

      const productId = this.dataset.productId;

      fetch("/create_transaction", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ product_id: productId })
      })
      .then(response => response.json())
      .then(data => {
        if (data.token) {
          snap.pay(data.token);
        } else {
          alert("Failed to process transaction.");
        }
      })
      .catch(error => {
        console.error("Error:", error);
        alert("Terjadi kesalahan.");
      });
    });
  }
});
