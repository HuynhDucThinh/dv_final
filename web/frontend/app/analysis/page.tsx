import type { Metadata } from 'next';
import { AIAnalysisPage } from '@/components/ai-analysis/AIAnalysisPage';

export const metadata: Metadata = {
  title: 'Phân tích Dữ liệu AI | Car Data Assistant',
  description: 'Trợ lý AI phân tích dữ liệu ô tô Việt Nam — viết code, chỉnh sửa, phê duyệt và thực thi.',
};

export default function AnalysisPage() {
  return (
    <div className="h-screen">
      <AIAnalysisPage />
    </div>
  );
}
