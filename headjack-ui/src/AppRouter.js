import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import SummaryPage from "./pages/SummaryPage";
import MetricsPage from "./pages/MetricsPage";
import PeoplePage from "./pages/PeoplePage";
import MessagesPage from "./pages/MessagesPage";
import ChatPage from "./pages/ChatPage";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SummaryPage />} />
        <Route path="metrics" element={<MetricsPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="people" element={<PeoplePage />} />
        <Route path="messages" element={<MessagesPage />} />
      </Routes>
    </BrowserRouter>
  );
}
