const { defineConfig } = require('eslint/config');
const eslintJs = require('@eslint/js');
const jestPlugin = require('eslint-plugin-jest');
const lwcConfig = require('@salesforce/eslint-config-lwc/recommended');
const globals = require('globals');

module.exports = defineConfig([
    // LWC 컴포넌트: Salesforce 권장 규칙
    {
        files: ['**/lwc/**/*.js'],
        extends: [lwcConfig]
    },

    // LWC 테스트 파일: Node 전역(require 등) 허용
    {
        files: ['**/lwc/**/*.test.js'],
        extends: [lwcConfig],
        rules: {
            '@lwc/lwc/no-unexpected-wire-adapter-usages': 'off',
            // 테스트에서는 타이머로 기다리고, document를 직접 다루고, jest.mock 안에서 mock* 이름을 다시 쓴다
            '@lwc/lwc/no-async-operation': 'off',
            '@lwc/lwc/no-document-query': 'off',
            'no-await-in-loop': 'off',
            'no-shadow': 'off'
        },
        languageOptions: {
            globals: {
                ...globals.node
            }
        }
    },

    // 테스트 전용 Mock(jest-mocks/)
    {
        files: ['**/jest-mocks/**/*.js'],
        languageOptions: {
            sourceType: 'module',
            ecmaVersion: 'latest',
            globals: {
                ...globals.node,
                ...globals.es2021,
                ...jestPlugin.environments.globals.globals
            }
        },
        plugins: {
            eslintJs
        },
        extends: ['eslintJs/recommended']
    }
]);
