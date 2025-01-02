namespace DOKUSHArp.Web.Components.Store;

public sealed class State<TState>(Store store) where TState : class, IState<TState>
{
	public TState Value => store.GetState<TState>();

	public Task UpdateAsync(Func<TState, TState> updateFunc) => store.UpdateStateAsync(updateFunc);
}