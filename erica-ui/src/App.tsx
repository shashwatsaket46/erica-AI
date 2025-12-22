import { useState } from "react";
import "./index.css";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import { askErica } from "./api";

interface Msg {
  sender: "user" | "erica";
  text: string;
}

export default function App() {
  const [messages, setMessages] = useState<Msg[]>([
    { sender: "erica", text: "Hi! I'm Erica, your AI tutor." }
  ]);

  const sendMessage = async (text: string) => {
    setMessages((m) => [...m, { sender: "user", text }]);

    try {
      const response = await askErica(text);
      const parts = [
        response.answer,
        response.context_used,
        JSON.stringify(response.citations, null, 2),
        JSON.stringify(response.subgraph, null, 2)
      ].filter(Boolean);

      const txt = parts.join("\n\n") || "No response";



      setMessages((m) => [...m, { sender: "erica", text: txt }]);
    } catch {
      setMessages((m) => [
        ...m,
        { sender: "erica", text: "Backend error." }
      ]);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {messages.map((msg, i) => (
          <ChatMessage key={i} sender={msg.sender} text={msg.text} />
        ))}
      </div>
      <ChatInput onSend={sendMessage} />
    </div>
  );
}
