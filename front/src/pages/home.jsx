import Home from "./pages/home.jsx";
import Privacy from "./pages/privacy.jsx";
import Terms from "./pages/terms.jsx";
import { Routes, Route } from "react-router-dom";
import "./App.css";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/terms" element={<Terms />} />
      <Route path="*" element={<Home />} />
    </Routes>
  );
}

export default App;
