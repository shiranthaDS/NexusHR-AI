export interface Message {
  id: string;
  question: string;
  answer: string;
  sources?: Source[];
  intent?: string;
  suggestions?: string[];
  timestamp: Date;
}

export interface Source {
  content: string;
  metadata: {
    filename: string;
    page: number;
    document_type: string;
    [key: string]: any;
  };
}

export interface Document {
  filename: string;
  size: number;
  uploaded_at: string;
}

export interface User {
  username: string;
  email: string;
  full_name: string;
  role: string;
  disabled: boolean;
}
