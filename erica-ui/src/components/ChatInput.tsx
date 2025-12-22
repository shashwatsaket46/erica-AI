import { useState } from "react";
import "./ChatInput.css";

export default function ChatInput({ onSend }: { onSend: (t: string) => void }) {
  const [value, setValue] = useState("");

  const send = () => {
    if (!value.trim()) return;
    onSend(value);
    setValue("");
  };

  return (
    <div className="chat-input-container">
      <input
        className="chat-input"
        placeholder="Ask something…"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && send()}
      />
      <button className="send-btn" onClick={send}>
        Send
      </button>
    </div>
  );
}
