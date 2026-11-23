import { createResource, toast } from "frappe-ui";

export const createAction = ({ success, onSuccess, onError, ...options }) =>
  createResource({
    ...options,
    onSuccess: (data) => {
      if (success) toast.success(success);
      onSuccess?.(data);
    },
    onError: (error) =>
      onError ? onError(error) : toast.error(error.messages?.[0] || "Something went wrong"),
  });
