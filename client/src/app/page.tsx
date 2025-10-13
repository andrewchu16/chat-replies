import ChatContainer from "../components/ChatContainer";

export default function Home() {
  return (
    <div className="h-screen bg-white text-black">
      <main className="mx-auto max-w-2xl px-4 sm:px-6 md:px-8 py-12">
        <ChatContainer />
      </main>
    </div>
  );
}
