import { useState } from "react";
import { Link } from "@tanstack/react-router";
import type { TaskResponse, StatusResponse } from "../../api/generated";
import { formatDate } from "../../lib/format";
import { DeleteConfirmModal } from "./DeleteConfirmModal";

type Props = {
  task: TaskResponse;
  status?: StatusResponse;
  onDelete: (id: number) => void;
};

function contrastText(hex: string): "#fff" | "#000" {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  // relative luminance (simplified sRGB)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? "#000" : "#fff";
}

export function TaskItem({ task, status, onDelete }: Props) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const isOverdue = new Date(task.due_date) < new Date(new Date().toDateString());

  return (
    <div className={`py-4 px-4 hover:bg-black/5 transition-colors ${isOverdue ? "bg-error/5" : "bg-white"}`}>
      {/* 1行目: タイトル + ステータス + 締切日 */}
      <div className="flex items-center justify-between">
        <Link
          to="/tasks/$taskId/edit"
          params={{ taskId: String(task.id) }}
          state={{ from: window.location.search }}
          className="font-semibold link link-hover"
        >
          {task.title}
        </Link>
        <div className="flex items-center gap-2">
          {status && (
            <span
              className="badge badge-sm"
              style={{ backgroundColor: status.color, color: contrastText(status.color) }}
            >
              {status.name}
            </span>
          )}
          <span className={`text-xs ${isOverdue ? "text-error font-semibold" : "text-base-content/50"}`}>
            締切: {formatDate(task.due_date)}
          </span>
        </div>
      </div>

      {/* 2行目: 内容 */}
      {task.content && (
        <p className="text-xs text-base-content/40 truncate max-w-xs mt-1">{task.content}</p>
      )}

      {/* 3行目: 作成日・更新日 + 操作 */}
      <div className="flex items-center justify-between mt-1">
        <div className="flex items-center gap-3 text-xs text-base-content/40">
          <span>作成: {formatDate(task.created_at)}</span>
          <span>更新: {formatDate(task.updated_at)}</span>
        </div>
        <div className="flex gap-1">
          <Link
            to="/tasks/$taskId/edit"
            params={{ taskId: String(task.id) }}
            state={{ from: window.location.search }}
            className="btn btn-ghost btn-xs"
          >
            編集
          </Link>
          <button
            className="btn btn-ghost btn-xs text-error"
            onClick={() => setIsModalOpen(true)}
          >
            削除
          </button>
        </div>
      </div>

      <DeleteConfirmModal
        title={task.title}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirm={() => onDelete(task.id)}
      />
    </div>
  );
}
