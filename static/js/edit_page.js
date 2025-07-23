document.addEventListener("DOMContentLoaded", () => {
  const deleteBtn = document.getElementById("deleteBtn");

  if (deleteBtn) {
    deleteBtn.addEventListener("click", () => {
      const konfirmasi = confirm("Are you sure you want to delete this product?");
      if (konfirmasi) {
        const productId = deleteBtn.getAttribute("data-id");

        fetch(`/delete/${productId}`, {
          method: "POST",
        })
          .then((res) => res.json())
          .then((data) => {
            if (data.status === "success") {
              window.location.href = "/dashboard/all";
            }
          });
      }
    });
  }
});
