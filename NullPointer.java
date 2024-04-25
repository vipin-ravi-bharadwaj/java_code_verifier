public class NullPointer {
    /*
 * Origin of the benchmark:
 *     repo: https://github.com/diffblue/cbmc.git
 *     branch: develop
 *     directory: regression/cbmc-java/NullPointerException1
 * The benchmark was taken from the repo: 24 January 2018
 */

  public static void main(String[] args)
  {
    Object o=null;
    try
    {
      o.hashCode();
      // should pass
      assert false;
    }
    catch(Exception e)
    {
    }
  }
};

