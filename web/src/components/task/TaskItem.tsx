import { useState } from "react";
import { Link } from "@tanstack/react-router";
import type { TaskResponse, StatusResponse } from "../../api/generated";
import { DeleteConfirmModal } from "./DeleteConfirmModal";

type Props = {
  task: TaskResponse;
  status?: StatusResponse;
  onDelete: (id: number) => void;
};

export function TaskItem({ task, status, onDelete }: Props) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const isOverdue = new Date(task.due_date) < new Date(new Date().toDateString());

  return (
    <tr>
      <td className="font-medium">{task.title}</td>
      <td className="max-w-xs truncate text-base-content/60">
        {task.content || "—"}
      </td>
      <td>
        {status ? (
          <span
            className="badge badge-sm"
            style={{ backgroundColor: status.color, color: "#fff" }}
          >
            {status.name}
          </span>
        ) : (
          "—"
        )}
      </td>
      <td>
        <span className={isOverdue ? "text-error font-semibold" : ""}>
          {task.due_date}
        </span>
      </td>
      <td>
        <div className="flex gap-1">
          <Link
            to="/tasks/$taskId/edit"
            params={{ taskId: String(task.id) }}
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
        <DeleteConfirmModal
          title={task.title}
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onConfirm={() => onDelete(task.id)}
        />
      </td>
    </tr>
  );
}