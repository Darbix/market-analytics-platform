import '@testing-library/jest-dom';

// Mock canvas for tests
HTMLCanvasElement.prototype.getContext = jest.fn();

jest.mock("react-chartjs-2", () => ({
  Line: jest.fn(() => null),
  Bar: jest.fn(() => null),
  Pie: jest.fn(() => null),
}));
