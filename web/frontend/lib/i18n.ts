import i18n from "i18next";
import { initReactI18next } from "react-i18next";

// =======================
// Tiếng Việt (Mặc định)
// =======================
const vi = {
  translation: {
    sidebar: {
      newChat: "Đoạn chat mới",
      history: "Lịch sử Chat",
      admin: "Quản trị",
      carData: "Dữ liệu Ô tô Việt Nam",
      libraryData: "Thư viện",
      today: "Hôm nay",
      yesterday: "Hôm qua",
      last7Days: "7 ngày trước",
      thisMonth: "Tháng này",
      older: "Cũ hơn",
      library: "Thư viện",
    },
    chat: {
      placeholder: "Hỏi về xe, thông số kỹ thuật, hoặc tính năng...",
      placeholderCar: "Hỏi về ô tô, giá xe, phân tích dữ liệu...",
      processing: "Đang xử lý yêu cầu...",
      listening: "Đang nghe...",
      disclaimer:
        "AI có thể cung cấp thông tin không chính xác. Hãy luôn kiểm tra lại dữ liệu quan trọng.",
      dataSources: "Nguồn tham khảo",
      noSources: "Không có tài liệu trích dẫn cho đoạn chat này.",
      sendTooltip: "Gửi câu hỏi",
      stopTooltip: "Dừng tạo câu trả lời (Enter)",
      micTooltip: "Nhập bằng giọng nói",
      scrollDown: "Cuộn xuống",
      carSystemHeader: "Hệ thống phân tích dữ liệu ô tô",
      copyAction: "Sao chép",
      copiedAction: "Đã chép",
      explainAction: "Giải thích lại",
      retryAction: "Thử lại",
      feedbackTitle: "Vấn đề bạn gặp phải?",
      feedbackReason1: "Sai thông số kỹ thuật",
      feedbackReason2: "Dữ liệu cũ/Không chính xác",
      feedbackReason3: "Không liên quan",
      feedbackReason4: "Khác",
      feedbackPlaceholder: "Góp ý thêm (không bắt buộc)...",
      feedbackCancel: "Hủy",
      feedbackSubmit: "Gửi",
    },
    admin: {
      systemAdmin: "Quản trị hệ thống",
      systemAdminDesc: "Thống kê & Cài đặt hệ thống",
      analyticsTab: "Thống kê & Lịch sử",
      aiConfigTab: "Cấu hình AI",
      totalInteractions: "Tổng lượt hội thoại",
      today: "Hôm nay",
      recentChats: "Lịch sử trò chuyện gần đây",
      noChats: "Chưa có lịch sử hội thoại nào",
      restoreConfigConfirm:
        "Khôi phục cấu hình AI mặc định? Điều này sẽ xóa các API key đã lưu và đặt lại các lựa chọn mô hình trên trình duyệt này.",
      aiConfig: "Cấu hình AI",
      aiConfigTitle: "Cấu hình AI & Tìm kiếm",
      aiConfigDesc:
        "Điều chỉnh cấu hình mặc định dùng cho các câu hỏi mới trên trình duyệt này.",
      default: "Mặc định",
      saveConfig: "Lưu cấu hình",
      saved: "Đã lưu",
      providerCreds: "Thông tin xác thực API",
      providerCredsDesc:
        "API keys được lưu cục bộ trên trình duyệt này và chỉ được gửi kèm khi có yêu cầu.",
      rememberDevice: "Lưu trên thiết bị này",
      inferenceRoles: "Phân quyền mô hình",
      inferenceRolesDesc:
        "Bạn có thể dùng các mô hình khác nhau cho việc sinh câu trả lời, viết lại câu hỏi, và tóm tắt.",
      useSameModel: "Sử dụng chung mô hình cho mọi tác vụ",
      defaultModel: "Mô hình trả lời mặc định",
      defaultModelDesc:
        "Hệ thống sẽ dùng cấu hình dự phòng đã thiết lập trên server nếu có lỗi.",
      temperatureLabel: "Temperature (Độ sáng tạo)",
      temperatureDesc:
        "Độ sáng tạo của câu trả lời. Hệ thống dữ liệu nên dùng 0.1–0.3.",
      maxTokensLabel: "Số từ tối đa (Max Tokens)",
      maxTokensDesc: "Giới hạn độ dài tối đa cho câu trả lời.",
    },
    setup: {
      title: "Thiết lập AI Inference",
      subtitle:
        "Vui lòng cung cấp API key cho các nhà cung cấp bạn muốn sử dụng.",
    },
    settings: {
      models: "CHỌN MÔ HÌNH AI",
      noApiKey:
        "Mô hình này chưa có API Key! Vui lòng chọn mô hình khác (ví dụ: GPT-4o Mini, Gemini 1.5).",
      params: "CẤU HÌNH",
      language: "NGÔN NGỮ",
      configTitle: "CẤU HÌNH LLM & TÌM KIẾM",
      tempDesc: "Điều chỉnh độ sáng tạo của câu trả lời.",
      maxTokensDesc: "Giới hạn độ dài tối đa (số từ) của câu trả lời.",
      openFullConfig: "Mở cấu hình đầy đủ →",
      selectModel: "CHỌN MÔ HÌNH AI",
    },
  },
};

// =======================
// English
// =======================
const en = {
  translation: {
    sidebar: {
      newChat: "New Chat",
      history: "Chat History",
      admin: "Admin",
      carData: "Vietnam Car Data",
      libraryData: "Library",
      today: "Today",
      yesterday: "Yesterday",
      last7Days: "Previous 7 Days",
      thisMonth: "This Month",
      older: "Older",
      library: "Library",
    },
    chat: {
      placeholder: "Ask about cars, specifications, or features...",
      placeholderCar: "Ask about cars, prices, data analysis...",
      processing: "Processing request...",
      listening: "Listening...",
      disclaimer:
        "AI can make mistakes. Consider verifying important information.",
      dataSources: "Sources",
      noSources: "No documents cited for this chat.",
      sendTooltip: "Send message",
      stopTooltip: "Stop generating (Enter)",
      micTooltip: "Voice input",
      scrollDown: "Scroll down",
      carSystemHeader: "Car Data Analysis System",
      copyAction: "Copy",
      copiedAction: "Copied",
      explainAction: "Explain again",
      retryAction: "Retry",
      feedbackTitle: "What's the issue?",
      feedbackReason1: "Incorrect technical specs",
      feedbackReason2: "Outdated/Inaccurate data",
      feedbackReason3: "Not relevant",
      feedbackReason4: "Other",
      feedbackPlaceholder: "Additional feedback (optional)...",
      feedbackCancel: "Cancel",
      feedbackSubmit: "Submit",
    },
    admin: {
      systemAdmin: "System Administration",
      systemAdminDesc: "Analytics & System Settings",
      analyticsTab: "Analytics & History",
      aiConfigTab: "AI Configuration",
      totalInteractions: "Total Interactions",
      today: "Today",
      recentChats: "Recent Chat History",
      noChats: "No chat history available",
      restoreConfigConfirm:
        "Restore default AI configuration? This will clear provider API keys and reset model selections on this browser.",
      aiConfig: "AI Configuration",
      aiConfigTitle: "AI & Search Settings",
      aiConfigDesc:
        "Adjust default configurations for new questions on this browser.",
      default: "Default",
      saveConfig: "Save Settings",
      saved: "Saved",
      providerCreds: "Provider Credentials",
      providerCredsDesc:
        "API keys are stored in this browser and sent only with inference requests.",
      rememberDevice: "Remember on this device",
      inferenceRoles: "Inference Roles",
      inferenceRolesDesc:
        "Answer generation, query rewriting, and memory summarization can use separate provider models.",
      useSameModel: "Use answer model for rewriter and memory summarizer",
      defaultModel: "Default Answer Model",
      defaultModelDesc:
        "The backend will use the configured fallback strategy.",
      temperatureLabel: "Temperature",
      temperatureDesc: "Creativity of the answer. 0.1–0.3 is recommended.",
      maxTokensLabel: "Max Tokens",
      maxTokensDesc: "Limit the maximum tokens for the answer.",
    },
    setup: {
      title: "AI Inference Setup",
      subtitle: "Please provide API keys for the providers you want to use.",
    },
    settings: {
      models: "SELECT AI MODEL",
      noApiKey:
        "This model is missing an API Key! Please select another model (e.g., GPT-4o Mini, Gemini 1.5).",
      params: "CONFIGURATION",
      language: "LANGUAGE",
      configTitle: "LLM & SEARCH CONFIG",
      tempDesc: "Adjust the creativity of the response.",
      maxTokensDesc: "Limit the maximum length (tokens) of the response.",
      openFullConfig: "Open full settings →",
      selectModel: "SELECT AI MODEL",
    },
  },
};

i18n.use(initReactI18next).init({
  resources: {
    vi,
    en,
  },
  lng: "vi", // Default language
  fallbackLng: "vi",
  interpolation: {
    escapeValue: false, // React already safes from xss
  },
});

export default i18n;
