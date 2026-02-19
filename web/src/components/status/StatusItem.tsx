import { useState } from "react";
import { Link } from "@tanstack/react-router";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import type { StatusResponse } from "../../api/generated";
import { DeleteConfirmModal } from "../task/DeleteConfirmModal";

type Props = {
  status: StatusResponse;
  onDelete: (id: number) => void;
};

export function SortableStatusItem({ status, onDelete }: Props) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: status.id });

  const style = {
    transform: CSS.Translate.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : undefined,
  };

  return (
    <tr ref={setNodeRef} style={style}>
      <td className="w-8 cursor-grab active:cursor-grabbing" {...attributes} {...listeners}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          className="w-5 h-5 text-base-content/40"
        >
          <path
            fillRule="evenodd"
            d="M2 4.75A.75.75 0 012.75 4h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 4.75zm0 5A.75.75 0 012.75 9h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 9.75zm0 5a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75a.75.75 0 01-.75-.75z"
            clipRule="evenodd"
          />
        </svg>
      </td>
      <td className="font-medium">{status.name}</td>
      <td>
        <span
          className="badge badge-sm"
          style={{ backgroundColor: status.color, color: "#fff" }}
        >
          {status.color}
        </span>
      </td>
      <td>
        <div className="flex gap-1">
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
