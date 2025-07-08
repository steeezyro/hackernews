import { Article } from "../types";

interface ArticleCardProps {
  article: Article;
  index: number;
}

export const ArticleCard = ({ article, index }: ArticleCardProps) => {
  const getStatusBadge = (status: Article["status"]) => {
    const badges = {
      success: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
      processing: "bg-yellow-100 text-yellow-800",
      screenshot_failed: "bg-orange-100 text-orange-800",
    };

    const labels = {
      success: "Success",
      failed: "Failed",
      processing: "Processing",
      screenshot_failed: "Preview Failed",
    };

    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium ${badges[status]}`}
      >
        {labels[status]}
      </span>
    );
  };

  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block bg-white rounded-lg shadow-md p-6 hover:shadow-xl hover:bg-blue-50 transition-all duration-200 cursor-pointer focus:outline-none"
    >
      <div className="flex items-start justify-between mb-3">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          #{index + 1}
        </span>
        {getStatusBadge(article.status)}
      </div>

      <h2 className="text-lg font-semibold text-gray-900 mb-3 line-clamp-2">
        {article.title}
      </h2>

      <p className="text-blue-600 hover:text-blue-800 text-sm mb-4 truncate">
        {article.url}
      </p>

      {article.status === "success" && article.screenshot ? (
        <div className="mb-4">
          <img
            src={`${import.meta.env.VITE_API_URL}${article.screenshot}`}
            alt={article.title}
            className="w-full h-48 object-cover rounded-md"
            loading="lazy"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = "none";
              target.nextElementSibling?.classList.remove("hidden");
            }}
          />
          <div className="hidden bg-gray-100 h-48 rounded-md flex items-center justify-center text-gray-500">
            <span>Preview unavailable</span>
          </div>
        </div>
      ) : (
        <div className="mb-4 bg-gray-100 h-48 rounded-md flex items-center justify-center text-gray-500">
          <span>
            {article.status === "processing"
              ? "Loading preview..."
              : "Preview unavailable"}
          </span>
        </div>
      )}

      <p className="text-gray-700 text-sm mb-4 line-clamp-3">
        {article.summary}
      </p>

      {article.updated_at && (
        <div className="flex justify-end">
          <span className="text-xs text-gray-500">
            Updated: {new Date(article.updated_at).toLocaleTimeString()}
          </span>
        </div>
      )}
    </a>
  );
};
