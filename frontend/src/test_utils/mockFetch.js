export const mockFetchSuccess = (data) => {
  fetch.mockResolvedValue({
    json: async () => data,
  });
};

export const mockFetchLoading = () => {
  fetch.mockImplementation(() => new Promise(() => {}));
};

export const mockFetchError = (message = "API down") => {
  fetch.mockRejectedValue(new Error(message));
};
