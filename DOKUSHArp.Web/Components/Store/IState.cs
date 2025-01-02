namespace DOKUSHArp.Web.Components.Store;

public interface IState<TSuper> where TSuper : class, IState<TSuper>
{
	public static abstract TSuper Default { get; }
}