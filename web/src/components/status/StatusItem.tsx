import { useState } from "react";
import { Link } from "@tanstack/react-router";
import type { StatusResponse } from "../../api/generated";
import { DeleteConfirmModal } from "../task/DeleteConfirmModal";

type Props = {
  status: StatusResponse;
  onDelete: (id: number) => void;
  onMoveUp?: () => void;
  onMoveDown?: () => void;
};

export function StatusItem({
  status,
  onDelete,
  onMoveUp,
  onMoveDown,
}: Props) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <tr>
      <td className="font-medium">{status.name}</td>
      <td>
        <span
          className="badge badge-sm"
          style={{ backgroundColor: status.color, color: "#fff" }}
        >
          {status.color}
        </span>
      </td>
      <td>{status.order}</td>
      <td>
        <div className="flex gap-1">
          {onMoveUp && (
            <button
              className="btn btn-ghost btn-xs"
              onClick={onMoveUp}
            >
              ↑
            </button>
          )}
          {onMoveDown && (
            <button
              className="btn btn-ghost btn-xs"
              onClick={onMoveDown}
            >
              ↓
            </button>
          )}
          <Link
            to="/statuses/$statusId/edit"
            params={{ statusId: String(status.id) }}
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
          title={status.name}
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onConfirm={() => onDelete(status.id)}
        />
      </td>
    </tr>
  );
}
