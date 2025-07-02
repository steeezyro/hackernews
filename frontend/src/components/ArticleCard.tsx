import { Article } from '../types';

interface ArticleCardProps {
  article: Article;
  index: number;
}

export const ArticleCard = ({ article, index }: ArticleCardProps) => {
  const speak = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1;
      utterance.pitch = 1;
      speechSynthesis.speak(utterance);
    }
  };

  const getStatusBadge = (status: Article['status']) => {
    const badges = {
      success: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      processing: 'bg-yellow-100 text-yellow-800',
      screenshot_failed: 'bg-orange-100 text-orange-800'
    };

    const labels = {
      success: 'Success',
      failed: 'Failed',
      processing: 'Processing',
      screenshot_failed: 'Preview Failed'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${badges[status]}`}>
        {labels[status]}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
      <div className="flex items-start justify-between mb-3">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          #{index + 1}
        </span>
        {getStatusBadge(article.status)}
      </div>
      
      <h2 className="text-lg font-semibold text-gray-900 mb-3 line-clamp-2">
        {article.title}
      </h2>
      
      <a 
        href={article.url} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-blue-600 hover:text-blue-800 text-sm mb-4 block truncate"
      >
        {article.url}
      </a>
      
      {article.status === 'success' && article.screenshot ? (
        <div className="mb-4">
          <img
            src={`${import.meta.env.VITE_API_URL}${article.screenshot}`}
            alt={article.title}
            className="w-full h-48 object-cover rounded-md"
            loading="lazy"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
              target.nextElementSibling?.classList.remove('hidden');
            }}
          />
          <div className="hidden bg-gray-100 h-48 rounded-md flex items-center justify-center text-gray-500">
            <span>Preview unavailable</span>
          </div>
        </div>
      ) : (
        <div className="mb-4 bg-gray-100 h-48 rounded-md flex items-center justify-center text-gray-500">
          <span>
            {article.status === 'processing' ? 'Loading preview...' : 'Preview unavailable'}
          </span>
        </div>
      )}
      
      <p className="text-gray-700 text-sm mb-4 line-clamp-3">
        {article.summary}
      </p>
      
      <div className="flex items-center justify-between">
        <button
          onClick={() => speak(article.summary)}
          className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          disabled={!article.summary}
        >
          🔊 Play Summary
        </button>
        
        {article.updated_at && (
          <span className="text-xs text-gray-500">
            Updated: {new Date(article.updated_at).toLocaleTimeString()}
          </span>
        )}
      </div>
    </div>
  );
};