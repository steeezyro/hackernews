import { useState, useEffect, useCallback } from 'react';
import { Article, ApiResponse, RefreshStatus } from '../types';

const API_BASE = import.meta.env.VITE_API_URL;

export const useArticles = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [refreshStatus, setRefreshStatus] = useState<RefreshStatus>({
    isRefreshing: false,
    lastRefresh: null,
    error: null
  });
  const [loading, setLoading] = useState(true);

  const fetchArticles = useCallback(async () => {
    try {
      setRefreshStatus(prev => ({ ...prev, error: null }));
      console.log('Fetching from:', `${API_BASE}/api/articles`);
      
      let response = await fetch(`${API_BASE}/api/articles`);
      console.log('Response status:', response.status);
      
      // If new endpoint fails, try legacy endpoint
      if (!response.ok) {
        console.log('Trying legacy endpoint...');
        response = await fetch(`${API_BASE}/api/results`);
        console.log('Legacy response status:', response.status);
      }
      
      if (!response.ok) {
        throw new Error(`Failed to fetch articles: ${response.status}`);
      }
      
      const data: any = await response.json();
      console.log('Received data:', data);
      
      // Handle both new format {articles: [...]} and old format [...]
      const articles = Array.isArray(data) ? data : (data.articles || []);
      console.log('Parsed articles:', articles);
      
      setArticles(articles);
      setRefreshStatus(prev => ({ 
        ...prev, 
        lastRefresh: data.cache_status?.latest_update ? new Date(data.cache_status.latest_update) : new Date()
      }));
      
    } catch (error) {
      console.error('Failed to fetch articles:', error);
      setRefreshStatus(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : 'Failed to fetch articles' 
      }));
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshArticles = useCallback(async () => {
    try {
      setRefreshStatus(prev => ({ ...prev, isRefreshing: true, error: null }));
      
      const response = await fetch(`${API_BASE}/api/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        if (response.status === 429) {
          const errorData = await response.json();
          throw new Error(errorData.detail?.error || 'Rate limit exceeded. Please try again later.');
        }
        throw new Error(`Refresh failed: ${response.status}`);
      }

      const data: ApiResponse = await response.json();
      
      if (data.status === 'cached') {
        // Immediate update with cached data
        setArticles(data.articles || []);
        setRefreshStatus(prev => ({ 
          ...prev, 
          isRefreshing: false,
          lastRefresh: new Date()
        }));
      } else {
        // Background refresh started, poll for updates
        setTimeout(() => {
          fetchArticles();
          setRefreshStatus(prev => ({ ...prev, isRefreshing: false }));
        }, 3000);
      }
      
    } catch (error) {
      console.error('Failed to refresh articles:', error);
      setRefreshStatus(prev => ({ 
        ...prev, 
        isRefreshing: false,
        error: error instanceof Error ? error.message : 'Failed to refresh articles' 
      }));
    }
  }, [fetchArticles]);

  useEffect(() => {
    fetchArticles();
  }, [fetchArticles]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(fetchArticles, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchArticles]);

  return {
    articles,
    refreshStatus,
    loading,
    refreshArticles,
    fetchArticles
  };
};