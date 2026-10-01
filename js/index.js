const traceForm = document.getElementById("trace-search");
const traceInput = document.getElementById("trace-code");
const traceButton = traceForm?.querySelector("button");

traceButton?.addEventListener("click", () => {
  const value = traceInput.value.trim();
  if (!value) {
    traceInput.focus();
    return;
  }
  window.location.href = `./public/trace.html?trace=${encodeURIComponent(value)}`;
});
traceForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  traceButton?.click();
});
