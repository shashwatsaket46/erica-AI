import "./ChatMessage.css";

export default function ChatMessage({
  sender,
  text
}: {
  sender: "user" | "erica";
  text: string;
}) {
  return (
    <div className={`chat-message ${sender}`}>
      <div className="bubble">{text}</div>
    </div>
  );
}
