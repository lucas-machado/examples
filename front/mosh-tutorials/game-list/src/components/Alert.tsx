import type { ReactNode } from "react";

interface AlertProps {
  children: ReactNode;
  OnClose: () => void;
}

const Alert = ({ children, OnClose }: AlertProps) => {
  return (
    <div className="alert alert-primary alert-dismissible">
      {children}
      <button
        type="button"
        className="btn-close"
        data-bs-dismiss="alert"
        aria-label="Close"
        onClick={OnClose}
      ></button>
    </div>
  );
};

export default Alert;
