let cart = [];
let total = 0;

function add(id, name, price) {
  let item = cart.find(i => i.id === id);
  if (item) item.qty++;
  else cart.push({id, name, price, qty: 1});
  render();
}

function render() {
  let list = document.getElementById("items");
  list.innerHTML = "";
  total = 0;
  cart.forEach(i => {
    total += i.price * i.qty;
    list.innerHTML += `<li>${i.name} x${i.qty}</li>`;
  });
  document.getElementById("total").innerText = total.toFixed(2);
}

function checkout() {
  fetch("/order", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(cart)
  })
  .then(r => r.json())
  .then(d => {
    window.location.href = "/pay/" + d.order_id;
  });
}
