package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

func main() {
	s := server.NewMCPServer(
		"knowledge_base",
		"0.1.0",
	)

	// Tool: list_files
	s.AddTool(mcp.NewTool("list_files",
		mcp.WithDescription("List files in a given directory path"),
		mcp.WithString("path", mcp.Required(), mcp.Description("The absolute path to the directory")),
	), func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		args, ok := request.Params.Arguments.(map[string]any)
		if !ok {
			return mcp.NewToolResultError("invalid arguments"), nil
		}
		dirPath, ok := args["path"].(string)
		if !ok {
			return mcp.NewToolResultError("path is required and must be a string"), nil
		}
		entries, err := os.ReadDir(dirPath)
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("failed to read dir: %v", err)), nil
		}

		var files []string
		for _, e := range entries {
			if !e.IsDir() {
				files = append(files, e.Name())
			}
		}
		
		result := fmt.Sprintf("Files in %s:\n%s", dirPath, strings.Join(files, "\n"))
		return mcp.NewToolResultText(result), nil
	})

	// Tool: read_content
	s.AddTool(mcp.NewTool("read_content",
		mcp.WithDescription("Read the textual content of a specific file"),
		mcp.WithString("path", mcp.Required(), mcp.Description("The absolute path to the file")),
	), func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		args, ok := request.Params.Arguments.(map[string]any)
		if !ok {
			return mcp.NewToolResultError("invalid arguments"), nil
		}
		filePath, ok := args["path"].(string)
		if !ok {
			return mcp.NewToolResultError("path is required and must be a string"), nil
		}
		data, err := os.ReadFile(filepath.Clean(filePath))
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("failed to read file: %v", err)), nil
		}
		return mcp.NewToolResultText(string(data)), nil
	})

	// Start standard IO server
	if err := server.ServeStdio(s); err != nil {
		fmt.Fprintf(os.Stderr, "Server error: %v\n", err)
		os.Exit(1)
	}
}
