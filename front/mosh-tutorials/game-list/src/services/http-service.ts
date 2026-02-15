import apiClient from "./api-client";

interface Entity {
  id: number;
}

class HttpService {
  endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  getAll<T>() {
    const controller = new AbortController();

    const request = apiClient.get<T[]>(this.endpoint, {
      signal: controller.signal,
    });

    return { request, cancel: () => controller.abort() };
  }

  add<T>(element: T) {
    const controller = new AbortController();

    const request = apiClient.post(this.endpoint, element, {
      signal: controller.signal,
    });

    return { request, cancel: () => controller.abort() };
  }

  delete(id: number) {
    const controller = new AbortController();

    const request = apiClient.delete(this.endpoint + "/" + id, {
      signal: controller.signal,
    });

    return { request, cancel: () => controller.abort() };
  }

  update<T extends Entity>(element: T) {
    const controller = new AbortController();

    const request = apiClient.patch(this.endpoint + "/" + element.id, element, {
      signal: controller.signal,
    });

    return { request, cancel: () => controller.abort() };
  }
}

const create = (endpoint: string) => new HttpService(endpoint);

export default create;
