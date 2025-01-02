using Microsoft.AspNetCore.Components;

namespace DOKUSHArp.Web.Components.Data;

public abstract class LoaderComponent : ComponentBase
{
	protected override async Task OnInitializedAsync()
	{
		await base.OnInitializedAsync().ConfigureAwait(false);
		await LoadAsync().ConfigureAwait(false);
	}

	protected abstract Task LoadAsync();
}