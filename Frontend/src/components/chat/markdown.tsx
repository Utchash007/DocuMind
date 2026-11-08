import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styles from "@/components/chat/markdown.module.css";

const plugins = [remarkGfm];

export default function Markdown({ text }: { text: string }) {
  return <div className={styles.content}><ReactMarkdown remarkPlugins={plugins} skipHtml components={{ a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer">{children}</a> }}>{text}</ReactMarkdown></div>;
}
