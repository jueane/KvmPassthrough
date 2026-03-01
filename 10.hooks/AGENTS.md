# AGENTS.md

## 项目概述

这是一个使用 Bun 运行时的 TypeScript 项目。通过 `bun init` 创建，支持现代 JavaScript/TypeScript 开发。

## 构建与运行命令

### 安装依赖
```bash
bun install
```

### 运行项目
```bash
bun run index.ts
```

### 直接执行 TypeScript 文件
```bash
bun index.ts
```

### 类型检查
```bash
bun tsc --noEmit
```

### 重新初始化项目（谨慎使用）
```bash
bun init
```

## 代码风格指南

### TypeScript 配置

项目使用 `tsconfig.json` 中的以下关键配置：

- **严格模式**: 启用 `strict: true`
- **模块解析**: `bundler` 模式，支持导入 `.ts` 扩展名
- **目标环境**: `ESNext`
- **无编译输出**: `noEmit: true`

### 命名约定

- **文件**: 使用 camelCase 命名，如 `myFile.ts`
- **类/接口**: 使用 PascalCase，如 `MyClass`、`IUserService`
- **变量/函数**: 使用 camelCase，如 `userName`、`getData()`
- **常量**: 使用 UPPER_SNAKE_CASE 或 camelCase（如为配置）
- **私有成员**: 使用前缀 `_` 或不使用前缀（现代 TypeScript 优先不使用）

### 导入规范

```typescript
// 标准导入
import { foo } from "./foo";
import type { Foo } from "./foo";

// 外部包导入
import express from "express";

// 相对导入优于绝对导入
// 推荐
import { helper } from "./utils/helper";

// 不推荐
import { helper } from "src/utils/helper";
```

### 类型使用

- 启用 `noUncheckedIndexedAccess: true`，访问索引签名类型时需注意
- 启用 `noImplicitOverride: true`，重写父类方法时必须使用 `override` 修饰符
- 优先使用接口定义对象类型，联合类型使用类型别名
- 避免使用 `any`，使用 `unknown` 代替不确定的类型
- 函数返回类型应明确标注

```typescript
// 推荐
interface User {
  id: string;
  name: string;
}

function getUser(id: string): User {
  return { id, name: "test" };
}

// 索引访问需谨慎
type Rec = { [key: string]: number };
const val: number = rec["key"]; // 可能为 undefined
```

### 错误处理

- 使用 try-catch 捕获异步操作错误
- 区分可恢复错误和不可恢复错误
- 考虑使用 Result/Either 类型处理错误
- 记录错误日志时避免泄露敏感信息

```typescript
// 推荐模式
async function fetchData<T>(url: string): Promise<T> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json();
  } catch (error) {
    console.error("Fetch failed:", error);
    throw error;
  }
}
```

### 代码格式

- 使用 Bun 内置格式化（`bun fmt`）或 Prettier
- 语句结尾不使用分号（JavaScript 风格）
- 对象/数组末尾可加逗号（trailing comma）

### 函数设计

- 单一职责原则
- 参数数量控制在合理范围（过多时使用对象参数）
- 纯函数优先，便于测试

### 注释

- 复杂逻辑添加注释说明
- 使用 JSDoc 注释公共 API
- 避免显而易见的注释

### 导入排序（可配置）

1. 外部依赖
2. 内部模块导入
3. 类型导入

### 自动化

- 运行格式化: `bun fmt`
- 运行类型检查: `bun tsc --noEmit`

### 注意事项

- 项目无测试框架，如需添加可使用 `bun test` 或 Vitest
- 启用 `verbatimModuleSyntax` 需显式使用 `import type`
- 使用 `bun run` 执行 package.json 中的脚本
