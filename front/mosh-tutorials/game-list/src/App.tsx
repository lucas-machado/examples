import { CanceledError, AxiosError } from "./services/api-client";
import userService, { type User } from "./services/user-service";
import useUsers from "./hooks/useUsers";

export default function App() {
  const { users, error, isLoading, setUsers, setError } = useUsers();

  const deleteUserBtnClick = (user: User) => {
    setUsers(users.filter((u) => u.id !== user.id));
    const { request } = userService.delete(user.id);

    const deleteUser = async () => {
      try {
        await request;
        console.log("user " + user.name + " deleted");
      } catch (err) {
        if (err instanceof CanceledError) return;
        setError((err as AxiosError).message);
        setUsers((curr) => {
          return [...curr, user];
        });
      }
    };

    deleteUser();
  };

  const addUserBtnClick = async () => {
    const newUser = { id: 0, name: "Mosh" };

    setUsers([...users, newUser]);

    const { request, cancel } = userService.add<User>(newUser);

    const addUser = async () => {
      try {
        const res = await request;
        setUsers((curr) => curr.map((u) => (u === newUser ? res.data : u)));
      } catch (err) {
        if (err instanceof CanceledError) return;
        setError((err as AxiosError).message);
        setUsers((curr) => curr.filter((u) => u !== newUser));
      }
    };

    addUser();

    return cancel;
  };

  const updateUserBtnClick = async (user: User) => {
    const updatedUser = { ...user, name: user.name + "!" };
    setUsers(users.map((u) => (u.id !== user.id ? u : updatedUser)));

    const { request, cancel } = userService.update<User>(updatedUser);

    const updateUser = async () => {
      try {
        await request;
      } catch (err) {
        if (err instanceof CanceledError) return;
        setError((err as AxiosError).message);
        setUsers((curr) => curr.map((u) => (u.id == user.id ? user : u)));
      }
    };

    updateUser();

    return cancel;
  };

  return (
    <>
      {error && <p className="text-danger">{error}</p>}
      {isLoading && <div className="spinner-border"></div>}
      <button className="btn btn-primary mb-3" onClick={addUserBtnClick}>
        Add
      </button>
      <ul className="list-group">
        {users.map((user) => (
          <li
            className="list-group-item d-flex justify-content-between"
            key={user.id}
          >
            {user.name}
            <div>
              <button
                className="btn btn-secondary mx-1"
                onClick={() => updateUserBtnClick(user)}
              >
                Update
              </button>
              <button
                className="btn btn-outline-danger"
                onClick={() => deleteUserBtnClick(user)}
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </>
  );
}
