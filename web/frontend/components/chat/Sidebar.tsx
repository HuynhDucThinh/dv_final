import React, { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import {
  Plus,
  MessageSquare,
  Trash2,
  Car,
  PanelLeftClose,
  Search,
  Moon,
  Sun,
  LibraryBig,
  Settings,
  X,
  Pin,
  PinOff,
} from "lucide-react";
import { useTheme } from "next-themes";
import Link from "next/link";
import { isToday, isYesterday, differenceInDays, isThisMonth } from "date-fns";
import type { ChatSession } from "@/lib/types";
import { useTranslation } from "react-i18next";
import { LanguageSelector } from "./LanguageSelector";
import { UserMenu } from "@/components/auth/UserMenu";

export type { ChatSession } from "@/lib/types";

interface SidebarProps {
  sessions: ChatSession[];
  currentSessionId: string | null;
  onNewChat: () => void;
  onSelectSession: (id: string) => void;
  onDeleteSession: (id: string) => void;
  onRenameSession: (id: string, newTitle: string) => void;
  onTogglePinSession?: (id: string, isPinned: boolean) => void;
  onCloseSidebar: () => void;
  isSessionsListLoading?: boolean;
}

export function Sidebar({
  sessions,
  currentSessionId,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  onRenameSession,
  onTogglePinSession,
  onCloseSidebar,
  isSessionsListLoading = false,
}: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);

  // Double-click edit state
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const editInputRef = useRef<HTMLInputElement>(null);
  const [mounted, setMounted] = useState(false);
  const { t } = useTranslation();

  const { theme, setTheme, systemTheme } = useTheme();

  const currentTheme = theme === "system" ? systemTheme : theme;

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  const groupedSessions = filteredSessions.reduce(
    (acc, session) => {
      const date = new Date(session.timestamp);
      let group = t("sidebar.older", "Cũ hơn");
      
      if (session.is_pinned) {
        group = t("sidebar.pinned", "Đã ghim");
      } else if (isToday(date)) {
        group = t("sidebar.today", "Hôm nay");
      } else if (isYesterday(date)) {
        group = t("sidebar.yesterday", "Hôm qua");
      } else if (differenceInDays(new Date(), date) <= 7) {
        group = t("sidebar.last7Days", "7 ngày trước");
      } else if (isThisMonth(date)) {
        group = t("sidebar.thisMonth", "Tháng này");
      }

      if (!acc[group]) acc[group] = [];
      acc[group].push(session);
      return acc;
    },
    {} as Record<string, ChatSession[]>,
  );

  const groupOrder = [
    t("sidebar.pinned", "Đã ghim"),
    t("sidebar.today", "Hôm nay"),
    t("sidebar.yesterday", "Hôm qua"),
    t("sidebar.last7Days", "7 ngày trước"),
    t("sidebar.thisMonth", "Tháng này"),
    t("sidebar.older", "Cũ hơn"),
  ];

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (editingSessionId && editInputRef.current) {
      editInputRef.current.focus();
    }
  }, [editingSessionId]);

  const handleEditSubmit = () => {
    if (editingSessionId && editTitle.trim()) {
      onRenameSession(editingSessionId, editTitle.trim());
    }
    setEditingSessionId(null);
  };

  return (
    <div className="h-screen w-full flex flex-col font-sans border-r border-gray-200 dark:border-gray-800 transition-colors bg-[#F9F9F9] dark:bg-[#171717]">
      {/* Header with glassmorphism */}
      <div className="h-14 flex items-center justify-between px-4 mt-1 flex-shrink-0">
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-xl flex items-center justify-center shadow-lg shadow-orange-500/20"
            style={{ background: "linear-gradient(135deg, #f97316, #ea580c)" }}
          >
            <Car className="w-4 h-4 text-white" />
          </div>
          <div>
            <span className="text-sm font-bold text-gray-800 dark:text-white tracking-tight">
              VietCar AI
            </span>
            <span className="block text-[9px] font-medium text-orange-600 dark:text-orange-400 uppercase tracking-widest leading-none mt-0.5">
              Car Data Assistant
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setIsSearchModalOpen(true)}
            className="p-1.5 rounded-lg text-gray-500 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-white/8 transition-all"
            title="Tìm kiếm đoạn chat"
          >
            <Search className="w-4 h-4" />
          </button>
          <button
            onClick={onCloseSidebar}
            className="p-1.5 rounded-lg text-gray-500 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-white/8 transition-all"
            title="Đóng sidebar"
          >
            <PanelLeftClose className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="px-3 py-2 flex-shrink-0 space-y-2">
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-start gap-2 rounded-xl py-2.5 px-3 transition-all duration-200 bg-transparent hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-800 dark:text-gray-200 active:scale-98"
        >
          <Plus className="w-4 h-4" />
          <span className="text-[13px] font-semibold">
            {t("sidebar.newChat", "Đoạn chat mới")}
          </span>
        </button>
        <Link
          href="/docs"
          className="w-full flex items-center justify-start gap-2 rounded-xl py-2.5 px-3 transition-all duration-200 bg-transparent text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-800 active:scale-98"
        >
          <LibraryBig className="w-4 h-4" />
          <span className="text-[13px] font-semibold">
            {t("sidebar.libraryData", "Dữ liệu Tham khảo")}
          </span>
        </Link>
        <Link
          href="/admin"
          className="w-full flex items-center justify-start gap-2 rounded-xl py-2.5 px-3 transition-all duration-200 bg-transparent text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-800 active:scale-98 mt-2"
        >
          <Settings className="w-4 h-4" />
          <span className="text-[13px] font-semibold">
            {t("sidebar.admin", "Quản trị")}
          </span>
        </Link>
      </div>

      {/* Divider */}
      <div className="mx-4 mb-2 border-t border-gray-200 dark:border-white/5 flex-shrink-0" />

      {/* Session list */}
      <div className="flex-1 overflow-y-auto px-2 py-2 space-y-4 custom-scrollbar">
        {isSessionsListLoading ? (
          <div className="space-y-2 px-1 py-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="animate-pulse flex items-center px-3 py-2.5 rounded-xl bg-gray-100 dark:bg-white/5"
              >
                <div className="w-4 h-4 bg-gray-200 dark:bg-gray-700 rounded mr-2.5 flex-shrink-0"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="px-3 py-6 text-[12px] text-gray-400 dark:text-gray-600 text-center italic leading-relaxed">
            {searchQuery ? (
              t('sidebar.noSearchResults')
            ) : (
              <>
                {t('sidebar.noConversations')}
                <br />
                <span className="not-italic text-gray-400 dark:text-gray-500">
                  {t('sidebar.startNewChat')}
                </span>
              </>
            )}
          </div>
        ) : (
          groupOrder.map((group) => {
            const groupSessions = groupedSessions[group];
            if (!groupSessions || groupSessions.length === 0) return null;

            return (
              <div key={group} className="space-y-0.5">
                <div className="px-2 pt-1 pb-1.5 text-[10px] font-bold uppercase tracking-widest text-gray-400 dark:text-gray-600">
                  {group}
                </div>
                {groupSessions.map((session) => {
                  const isActive = currentSessionId === session.id;
                  const isEditing = editingSessionId === session.id;
                  return (
                    <div
                      key={session.id}
                      className={`group relative flex items-center px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200 ${
                        isActive
                          ? "bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                          : "hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                      }`}
                      onClick={() => !isEditing && onSelectSession(session.id)}
                    >
                      <MessageSquare
                        className={`w-3.5 h-3.5 mr-2.5 flex-shrink-0 transition-colors ${
                          isActive
                            ? "text-gray-900 dark:text-gray-100"
                            : "text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-200"
                        }`}
                      />
                      <div className="flex-1 truncate pr-6">
                        {isEditing ? (
                          <input
                            ref={editInputRef}
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            onBlur={handleEditSubmit}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") handleEditSubmit();
                              if (e.key === "Escape") setEditingSessionId(null);
                            }}
                            className={`w-full bg-transparent border-b border-blue-400 outline-none text-[12.5px] font-medium text-blue-700 dark:text-blue-300`}
                          />
                        ) : (
                          <span
                            onDoubleClick={(e) => {
                              e.stopPropagation();
                              setEditingSessionId(session.id);
                              setEditTitle(session.title);
                            }}
                            className={`text-[12.5px] font-medium block truncate select-none ${isActive ? "text-gray-900 dark:text-white" : ""}`}
                          >
                            {session.title}
                          </span>
                        )}
                      </div>
                      {onTogglePinSession && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onTogglePinSession(session.id, !session.is_pinned);
                          }}
                          className={`absolute right-8 p-1.5 rounded-lg transition-all opacity-0 group-hover:opacity-100 ${
                            session.is_pinned 
                              ? "text-blue-500 hover:bg-blue-500/10 opacity-100" 
                              : "text-gray-600 hover:text-blue-400 hover:bg-blue-400/10"
                          }`}
                          title={session.is_pinned ? t("sidebar.unpin", "Bỏ ghim") : t("sidebar.pin", "Ghim")}
                        >
                          {session.is_pinned ? <PinOff className="w-3 h-3" /> : <Pin className="w-3 h-3" />}
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSessionToDelete(session.id);
                        }}
                        className="absolute right-2 p-1.5 rounded-lg text-gray-600 hover:text-red-400 hover:bg-red-400/10 transition-all opacity-0 group-hover:opacity-100"
                        title={t("sidebar.deleteChat", "Xóa đoạn chat")}
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  );
                })}
              </div>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-200 dark:border-white/5 flex-shrink-0 space-y-3">
        {/* User auth area */}
        <UserMenu />

        {/* Bottom bar: label + controls */}
        <div className="flex items-center justify-between">
          <p className="text-xs font-semibold tracking-wide text-gray-500 dark:text-gray-400 leading-relaxed uppercase">
            {t("sidebar.carData", "Dữ liệu Ô tô Việt Nam")}
          </p>
          <div className="flex gap-2">
            <LanguageSelector />
            <button
              onClick={() => setTheme(currentTheme === "dark" ? "light" : "dark")}
              className="p-1.5 rounded-lg text-gray-500 dark:text-gray-500 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-800 transition-all"
              title="Chuyển chế độ giao diện"
            >
              {currentTheme === "dark" ? (
                <Sun className="w-4 h-4" />
              ) : (
                <Moon className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Search Modal (ChatGPT like) */}
      {mounted &&
        isSearchModalOpen &&
        createPortal(
          <div
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 dark:bg-black/60 px-4 backdrop-blur-sm"
            onClick={() => setIsSearchModalOpen(false)}
          >
            <div
              className="w-full max-w-2xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col transform transition-all animate-in zoom-in-95 duration-200"
              onClick={(e) => e.stopPropagation()}
              style={{ maxHeight: "80vh" }}
            >
              <div className="relative border-b border-gray-200 dark:border-gray-800">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  autoFocus
                  type="text"
                  placeholder="Tìm kiếm..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-transparent py-4 pl-12 pr-12 text-lg text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none"
                />
                <button
                  onClick={() => setIsSearchModalOpen(false)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
                <div className="px-3 pt-3 pb-2 text-xs font-semibold text-gray-500 dark:text-gray-400">
                  Đoạn chat gần đây
                </div>
                {filteredSessions.length === 0 ? (
                  <div className="p-8 text-center text-sm text-gray-500">
                    Không có đoạn chat nào phù hợp.
                  </div>
                ) : (
                  filteredSessions.map((session) => (
                    <button
                      key={session.id}
                      onClick={() => {
                        onSelectSession(session.id);
                        setIsSearchModalOpen(false);
                      }}
                      className="w-full flex items-center gap-3 px-3 py-3 text-left hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors"
                    >
                      <MessageSquare className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-200 truncate">
                        {session.title}
                      </span>
                    </button>
                  ))
                )}
              </div>
            </div>
          </div>,
          document.body,
        )}

      {/* Delete Confirmation Modal */}
      {mounted &&
        sessionToDelete &&
        createPortal(
          <div
            className="fixed inset-0 z-[110] flex items-center justify-center bg-black/40 dark:bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
            onClick={() => setSessionToDelete(null)}
          >
            <div
              className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-2xl p-6 w-[90%] max-w-sm transform transition-all animate-in zoom-in-95 duration-200"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="mb-4">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                  Xóa hội thoại?
                </h3>
              </div>

              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6 leading-relaxed">
                Bạn có chắc chắn muốn xóa đoạn hội thoại này không? Dữ liệu sẽ
                bị xóa hoàn toàn khỏi cơ sở dữ liệu và không thể khôi phục.
              </p>

              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setSessionToDelete(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-xl transition-colors"
                >
                  Hủy bỏ
                </button>
                <button
                  onClick={() => {
                    onDeleteSession(sessionToDelete);
                    setSessionToDelete(null);
                  }}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 shadow-md shadow-red-500/20 rounded-xl transition-colors"
                >
                  Xác nhận xóa
                </button>
              </div>
            </div>
          </div>,
          document.body,
        )}
    </div>
  );
}
