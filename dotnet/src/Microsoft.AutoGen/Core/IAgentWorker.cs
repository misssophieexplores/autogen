// Copyright (c) Microsoft Corporation. All rights reserved.
// IAgentWorker.cs
using Microsoft.AutoGen.Contracts;
namespace Microsoft.AutoGen.Core;

public interface IAgentWorker
{
    ValueTask PublishEventAsync(CloudEvent evt, CancellationToken cancellationToken = default);
    ValueTask SendRequestAsync(Agent agent, RpcRequest request, CancellationToken cancellationToken = default);
    ValueTask SendResponseAsync(RpcResponse response, CancellationToken cancellationToken = default);
    ValueTask SendMessageAsync(Message message, CancellationToken cancellationToken = default);
    ValueTask StoreAsync(AgentState value, CancellationToken cancellationToken = default);
    ValueTask<AgentState> ReadAsync(AgentId agentId, CancellationToken cancellationToken = default);
}
