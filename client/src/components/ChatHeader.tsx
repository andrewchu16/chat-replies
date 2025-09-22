interface ChatHeaderProps {
  title?: string;
}

export default function ChatHeader({ title = "Chat" }: ChatHeaderProps) {
  return (
    <h1 className="text-xl font-medium tracking-tight mb-8">
      {title}
    </h1>
  );
}
