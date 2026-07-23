import React, { useState } from "react";
import { Play, RotateCcw, Check, XCircle, SendHorizonal } from "lucide-react";
import { useTranslation } from "react-i18next";
import Editor from "react-simple-code-editor";
import Prism from "prismjs";
import "prismjs/themes/prism-tomorrow.css";
import "prismjs/components/prism-python";
import "prismjs/components/prism-sql";
import "prismjs/components/prism-bash";

interface InteractiveCodeBlockProps {
  initialCode: string;
  language?: string;
  sessionId?: string; // Để gửi lên backend
  onSendResult?: (code: string, output: string) => void; // Callback gửi kết quả cho AI
}

export function InteractiveCodeBlock({
  initialCode,
  language = "python",
  sessionId = "unknown",
  onSendResult,
}: InteractiveCodeBlockProps) {
  const { t } = useTranslation();
  const [code, setCode] = useState(initialCode);
  const [status, setStatus] = useState<
    "pending" | "executing" | "success" | "error"
  >("pending");
  const [output, setOutput] = useState<{
    stdout: string;
    stderr: string;
    images: string[];
    dfContext: string;
  } | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [sent, setSent] = useState(false); // Chống gửi kết quả 2 lần

  const handleExecute = async () => {
    setStatus("executing");
    setErrorMessage(null);
    setOutput(null);

    try {
      const res = await fetch("/api/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, session_id: sessionId, language }),
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        setStatus("error");
        setErrorMessage(data.error || data.details || "Lỗi thực thi mã");
        if (data.stdout || data.stderr) {
          setOutput({
            stdout: data.stdout || "",
            stderr: data.stderr || "",
            images: [],
            dfContext: "",
          });
        }
      } else {
        setStatus("success");
        setOutput({
          stdout: data.stdout || "",
          stderr: data.stderr || "",
          images: data.images || [],
          dfContext: data.df_context || "",
        });
      }
    } catch (err) {
      setStatus("error");
      setErrorMessage(err instanceof Error ? err.message : "Unknown error");
    }
  };

  const handleReset = () => {
    setCode(initialCode);
    setStatus("pending");
    setOutput(null);
    setErrorMessage(null);
    setSent(false);
  };

  const handleSendResult = () => {
    if (!onSendResult || !output?.stdout || sent) return;
    // Gửi stdout + df_context để AI biết trạng thái dữ liệu mới nhất
    const combinedOutput = output.dfContext
      ? `${output.stdout}\n\n${output.dfContext}`
      : output.stdout;
    onSendResult(code, combinedOutput);
    setSent(true);
  };

  const getStatusLabel = () => {
    switch (status) {
      case "pending":
        return "Chờ duyệt";
      case "executing":
        return "Đang chạy...";
      case "success":
        return "Thành công";
      case "error":
        return "Lỗi";
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case "pending":
        return "text-amber-500 bg-amber-500/10";
      case "executing":
        return "text-blue-500 bg-blue-500/10";
      case "success":
        return "text-emerald-500 bg-emerald-500/10";
      case "error":
        return "text-red-500 bg-red-500/10";
    }
  };

  // Chỉ hỗ trợ thực thi code Python
  const isPythonExecutable = ["python", "py", "python3"].includes(
    language.toLowerCase(),
  );
  return (
    <div className="my-4 border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden bg-white dark:bg-[#121212] shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-gray-50 dark:bg-[#1A1A1A] border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">
            {language}
          </span>
          <span
            className={`px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-md ${getStatusColor()}`}
          >
            {getStatusLabel()}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            disabled={status === "executing"}
            className="flex items-center gap-1.5 px-2 py-1 text-xs font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 disabled:opacity-50 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Làm lại
          </button>
          {isPythonExecutable ? (
            <button
              onClick={handleExecute}
              disabled={status === "executing"}
              className="flex items-center gap-1.5 px-3 py-1 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-md disabled:opacity-50 transition-colors shadow-sm"
            >
              <Play className="w-3.5 h-3.5" />
              Thực thi
            </button>
          ) : (
            <span className="px-3 py-1 text-xs font-medium text-gray-400 dark:text-gray-500 bg-gray-100 dark:bg-gray-800 rounded-md">
              Chỉ hỗ trợ thực thi Python
            </span>
          )}
        </div>
      </div>

      <div className="relative bg-[#2d2d2d]">
        <Editor
          value={code}
          onValueChange={(newCode) => {
            setCode(newCode);
            if (status !== "pending" && status !== "executing")
              setStatus("pending");
          }}
          highlight={(code) =>
            Prism.highlight(
              code,
              Prism.languages[language] || Prism.languages.javascript,
              language,
            )
          }
          padding={16}
          style={{
            fontFamily: '"Fira Code", "Fira Mono", Consolas, monospace',
            fontSize: 14,
            backgroundColor: "#2d2d2d",
            color: "#f8f8f2",
            minHeight: "120px",
          }}
          textareaClassName="focus:outline-none"
        />
      </div>

      {/* Output */}
      {status !== "pending" && (output || errorMessage) && (
        <div className="border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-[#1A1A1A] p-4">
          <h4 className="text-xs font-bold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
            Kết quả
          </h4>

          {errorMessage && (
            <div className="mb-3 flex items-start gap-2 text-red-600 dark:text-red-400 text-sm bg-red-500/10 p-3 rounded-lg">
              <XCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <pre className="whitespace-pre-wrap font-mono text-xs">
                {errorMessage}
              </pre>
            </div>
          )}

          {output?.stdout && (
            <div className="mb-3">
              <span className="text-[10px] text-gray-500 font-bold mb-1 block">
                STDOUT:
              </span>
              <pre className="p-3 bg-white dark:bg-[#121212] border border-gray-200 dark:border-gray-800 rounded-lg text-sm text-gray-800 dark:text-gray-200 font-mono overflow-x-auto">
                {output.stdout}
              </pre>

              {/* Snapshot DataFrame state — hiện để user thấy AI sẽ nhận thông tin gì */}
              {output.dfContext && (
                <div className="mt-2 px-3 py-2 bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 rounded-lg">
                  <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wide block mb-1">
                    Trạng thái DataFrame (sẽ gửi kèm cho AI)
                  </span>
                  <pre className="text-[11px] text-indigo-700 dark:text-indigo-300 font-mono whitespace-pre-wrap leading-relaxed">
                    {output.dfContext}
                  </pre>
                </div>
              )}

              {/* Nút gửi kết quả cho AI — chỉ hiện khi có callback và chưa gửi */}
              {onSendResult && (
                <button
                  onClick={handleSendResult}
                  disabled={sent}
                  className={`mt-2 flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                    sent
                      ? "text-emerald-600 bg-emerald-50 dark:bg-emerald-500/10 cursor-default"
                      : "text-indigo-600 bg-indigo-50 dark:bg-indigo-500/10 hover:bg-indigo-100 dark:hover:bg-indigo-500/20"
                  }`}
                >
                  {sent ? (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      Đã gửi cho AI
                    </>
                  ) : (
                    <>
                      <SendHorizonal className="w-3.5 h-3.5" />
                      Gửi kết quả cho AI
                    </>
                  )}
                </button>
              )}
            </div>
          )}

          {output?.stderr && (
            <div className="mb-3">
              <span className="text-[10px] text-red-500 font-bold mb-1 block">
                STDERR:
              </span>
              <pre className="p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 rounded-lg text-sm text-red-600 dark:text-red-400 font-mono overflow-x-auto">
                {output.stderr}
              </pre>
            </div>
          )}

          {output?.images && output.images.length > 0 && (
            <div className="space-y-3 mt-4">
              <span className="text-[10px] text-gray-500 font-bold block">
                BIỂU ĐỒ:
              </span>
              {output.images.map((img, idx) => (
                <div
                  key={idx}
                  className="bg-white dark:bg-[#121212] border border-gray-200 dark:border-gray-800 rounded-lg p-2 overflow-hidden shadow-sm"
                >
                  <img
                    src={`data:image/png;base64,${img}`}
                    alt={`Chart ${idx + 1}`}
                    className="max-w-full h-auto mx-auto rounded"
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
