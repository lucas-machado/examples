import { isRouteErrorResponse, useRouteError } from "react-router-dom";

const ErrorPage = () => {
  const error = useRouteError();

  console.log("oh no! something bad happened: " + error);

  return (
    <>
      <h1>Oops...</h1>
      <p>{isRouteErrorResponse(error) ? "Invalid page" : "Unexpected error"}</p>
    </>
  );
};

export default ErrorPage;
