import { useState } from "react";
import { useAuth } from "./context/AuthContext";
import Router from "./Routes";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <Router />
    </>
  );
}

export default App;
