using Microsoft.AspNetCore.Components;

namespace DOKUSHArp.Web.Components.Store;

public abstract class StatefulComponent : ComponentBase, IAsyncDisposable
{
	[Inject] protected Store Store { get; set; } = default!;

	public ValueTask DisposeAsync()
	{
		Store.DeregisterForUpdates(this);

		return default;
	}

	protected override void OnInitialized()
	{
		base.OnInitialized();

		Store.RegisterForUpdates(this);
	}

	internal Task TriggerUpdateAsync() => InvokeAsync(StateHasChanged);
}
