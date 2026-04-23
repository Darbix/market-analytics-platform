module.exports = {
  testEnvironment: "jsdom",
  setupFilesAfterEnv: [
    "<rootDir>/src/tests/setupTests.js",
    "<rootDir>/jest.setup.js"
  ],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  transform: {
    '^.+\\.jsx?$': 'babel-jest',
  },
  testPathIgnorePatterns: ['/node_modules/', '/dist/'],
};
