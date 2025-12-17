'use client';

import { useState, useRef, useEffect } from 'react';
import { chatAPI } from '@/lib/api';
import { Message } from '@/types';
import { 
  PaperAirplaneIcon,
  SparklesIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load initial suggestions
    loadSuggestions('What is the leave policy?');
  }, []);

  const loadSuggestions = async (question: string) => {
    try {
      const data = await chatAPI.getSuggestions(question);
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  const handleSubmit = async (question?: string) => {
    const queryText = question || input;
    if (!queryText.trim() || loading) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      question: queryText,
      answer: '',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInput('');
    setLoading(true);

    try {
      const chatHistory = messages.map((msg) => ({
        question: msg.question,
        answer: msg.answer,
      }));

      const response = await chatAPI.query(queryText, chatHistory, true);

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === newMessage.id
            ? {
                ...msg,
                answer: response.answer,
                sources: response.sources,
                intent: response.intent,
                suggestions: response.suggestions,
              }
            : msg
        )
      );

      if (response.suggestions) {
        setSuggestions(response.suggestions);
      }
    } catch (error: any) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === newMessage.id
            ? {
                ...msg,
                answer: 'Sorry, I encountered an error. Please try again.',
              }
            : msg
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSubmit(suggestion);
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center space-x-3">
          <SparklesIcon className="h-6 w-6 text-blue-600" />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">HR Assistant Chat</h2>
            <p className="text-sm text-gray-500">Ask me anything about HR policies</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <SparklesIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Welcome to NexusHR AI
            </h3>
            <p className="text-gray-500 mb-6">
              Ask me questions about company policies, leave, benefits, and more
            </p>
            
            {/* Initial Suggestions */}
            {suggestions.length > 0 && (
              <div className="max-w-2xl mx-auto">
                <p className="text-sm font-medium text-gray-700 mb-3">Try asking:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="px-4 py-3 bg-white border border-gray-200 rounded-lg text-sm text-left hover:border-blue-300 hover:bg-blue-50 transition-all"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className="space-y-4">
            {/* User Question */}
            <div className="flex justify-end">
              <div className="max-w-2xl bg-blue-600 text-white rounded-2xl px-5 py-3">
                <p className="text-sm">{message.question}</p>
              </div>
            </div>

            {/* AI Answer */}
            <div className="flex justify-start">
              <div className="max-w-3xl bg-white border border-gray-200 rounded-2xl px-5 py-4 space-y-4">
                {message.answer ? (
                  <>
                    <p className="text-gray-800 whitespace-pre-wrap">{message.answer}</p>
                    
                    {/* Sources */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="pt-4 border-t border-gray-100">
                        <p className="text-xs font-semibold text-gray-500 mb-2 flex items-center">
                          <DocumentTextIcon className="h-4 w-4 mr-1" />
                          SOURCES
                        </p>
                        <div className="space-y-2">
                          {message.sources.map((source, idx) => (
                            <div
                              key={idx}
                              className="bg-gray-50 rounded-lg p-3 text-xs"
                            >
                              <p className="text-gray-700 mb-1">
                                {source.content.substring(0, 150)}...
                              </p>
                              <p className="text-gray-500">
                                📄 {source.metadata.filename} • Page {source.metadata.page + 1}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Follow-up Suggestions */}
                    {message.suggestions && message.suggestions.length > 0 && (
                      <div className="pt-4 border-t border-gray-100">
                        <p className="text-xs font-semibold text-gray-500 mb-2">
                          FOLLOW-UP QUESTIONS
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {message.suggestions.map((suggestion, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleSuggestionClick(suggestion)}
                              className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full text-xs transition-all"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="flex items-center space-x-2">
                    <div className="animate-pulse flex space-x-1">
                      <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
                      <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
                      <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
                    </div>
                    <span className="text-sm text-gray-500">Thinking...</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
          className="max-w-4xl mx-auto"
        >
          <div className="flex space-x-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about HR policies..."
              disabled={loading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center space-x-2"
            >
              <span>Send</span>
              <PaperAirplaneIcon className="h-4 w-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
