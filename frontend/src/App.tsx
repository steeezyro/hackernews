import { useArticles } from './hooks/useArticles';
import { Header } from './components/Header';
import { ArticleCard } from './components/ArticleCard';
import { LoadingSpinner } from './components/LoadingSpinner';
import './index.css';

function App() {
  const { articles, refreshStatus, loading, refreshArticles } = useArticles();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading HackerNews stories...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        refreshStatus={refreshStatus}
        onRefresh={refreshArticles}
        articlesCount={articles.length}
      />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {articles.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No articles available</h3>
            <p className="mt-1 text-sm text-gray-500">Try refreshing to load the latest HackerNews stories.</p>
            <div className="mt-6">
              <button
                onClick={refreshArticles}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Load Stories
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article, index) => (
              <ArticleCard 
                key={`${article.url}-${article.updated_at}`} 
                article={article} 
                index={index} 
              />
            ))}
          </div>
        )}
        
        {refreshStatus.isRefreshing && (
          <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 border">
            <div className="flex items-center">
              <LoadingSpinner size="sm" className="mr-3" />
              <span className="text-sm text-gray-700">Refreshing stories...</span>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;