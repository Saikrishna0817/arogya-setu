import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

// Entry point for the SPA; the entire frontend is hard-coded in React components
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
